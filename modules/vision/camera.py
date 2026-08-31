import cv2


def main():
    # Cámara predeterminada de Windows
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    # Requisitos iniciales del proyecto
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    camera.set(cv2.CAP_PROP_FPS, 30)

    print("ZeroUI-AC")
    print("Cámara iniciada correctamente.")
    print("Presiona Q para cerrar.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("ERROR: No se pudo capturar el frame.")
                break

            cv2.imshow("ZeroUI-AC - Camara", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("Cámara cerrada correctamente.")


if __name__ == "__main__":
    main()