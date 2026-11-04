"""HTTP routes that delegate exclusively to ZeroUIApplicationFacade."""

from fastapi import APIRouter, HTTPException


def create_router(facade):
    router = APIRouter()

    def invoke(operation):
        try:
            return operation()
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Internal ZeroUI operation failed",
            ) from None

    @router.get("/health")
    def health():
        return {"status": "ok", "service": "zeroui-ac"}

    @router.get("/status")
    def status():
        return invoke(facade.get_system_status)

    @router.get("/session")
    def session():
        return invoke(facade.get_session_metrics)

    @router.get("/adaptation")
    def adaptation():
        return invoke(facade.get_adaptation_state)

    @router.get("/commands")
    def commands():
        return invoke(facade.get_commands)

    @router.post("/system/suspend")
    def suspend():
        return invoke(facade.suspend)

    @router.post("/system/activate")
    def activate():
        return invoke(facade.activate)

    @router.post("/commands/show")
    def show_commands():
        return invoke(facade.show_commands)

    @router.post("/commands/hide")
    def hide_commands():
        return invoke(facade.hide_commands)

    return router
