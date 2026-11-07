import {
  Component,
  OnInit,
  OnDestroy,
  signal
} from '@angular/core';

import {
  IonHeader,
  IonToolbar,
  IonTitle,
  IonContent,
  IonButton,
  IonCard,
  IonCardHeader,
  IonCardTitle,
  IonCardContent,
  IonSpinner
} from '@ionic/angular';

import {
  ZeroUiApiService
} from '../core/services/zero-ui-api.service';

import {
  SystemStatus
} from '../core/models/system-status.model';

import {
  AdaptationState
} from '../core/models/adaptation-state.model';

import {
  SessionMetrics
} from '../core/models/session-metrics.model';

import {
  CommandCatalog
} from '../core/models/command-catalog.model';

@Component({
  selector: 'app-home',
  templateUrl: 'home.page.html',
  styleUrls: ['home.page.scss'],
  standalone: true,

  imports: [
    IonHeader,
    IonToolbar,
    IonTitle,
    IonContent,
    IonButton,
    IonCard,
    IonCardHeader,
    IonCardTitle,
    IonCardContent,
    IonSpinner
  ]
})
export class HomePage implements OnInit, OnDestroy {

  // ==============================
  // ESTADO GENERAL
  // ==============================

  status = signal<SystemStatus | null>(null);

  adaptation = signal<AdaptationState | null>(null);

  session = signal<SessionMetrics | null>(null);

  commands = signal<CommandCatalog | null>(null);


  // ==============================
  // ESTADO DE INTERFAZ
  // ==============================

  loading = signal(false);

  error = signal(false);

  connected = signal(false);

  actionLoading = signal(false);

  actionMessage = signal('');


  // ==============================
  // ACTUALIZACIÓN AUTOMÁTICA
  // ==============================

  private refreshInterval:
    ReturnType<typeof setInterval> | null = null;


  constructor(
    private zeroUiApi: ZeroUiApiService
  ) {}


  // ==============================
  // CICLO DE VIDA
  // ==============================

  ngOnInit(): void {

    // Primera carga del dashboard
    this.refreshDashboard();

    // Actualización automática cada 5 segundos
    this.refreshInterval = setInterval(
      () => {

        this.refreshDashboard(false);

      },
      5000
    );

  }


  ngOnDestroy(): void {

    if (this.refreshInterval !== null) {

      clearInterval(
        this.refreshInterval
      );

      this.refreshInterval = null;

    }

  }


  // ==============================
  // DASHBOARD
  // ==============================

  refreshDashboard(
    showLoading: boolean = true
  ): void {

    this.loadStatus(showLoading);

    this.loadAdaptation();

    this.loadSession();

    this.loadCommands();

  }


  // ==============================
  // ESTADO DEL SISTEMA
  // ==============================

  loadStatus(
    showLoading: boolean = true
  ): void {

    if (showLoading) {

      this.loading.set(true);

    }

    this.zeroUiApi
      .getSystemStatus()
      .subscribe({

        next: (status) => {

          this.status.set(status);

          this.connected.set(true);

          this.error.set(false);

          this.loading.set(false);

        },

        error: () => {

          this.status.set(null);

          this.connected.set(false);

          this.error.set(true);

          this.loading.set(false);

        }

      });

  }


  // ==============================
  // ADAPTACIÓN INTELIGENTE
  // ==============================

  loadAdaptation(): void {

    this.zeroUiApi
      .getAdaptationState()
      .subscribe({

        next: (adaptation) => {

          this.adaptation.set(
            adaptation
          );

        },

        error: () => {

          this.adaptation.set(null);

        }

      });

  }


  // ==============================
  // MÉTRICAS DE SESIÓN
  // ==============================

  loadSession(): void {

    this.zeroUiApi
      .getSessionMetrics()
      .subscribe({

        next: (session) => {

          this.session.set(session);

        },

        error: () => {

          this.session.set(null);

        }

      });

  }


  // ==============================
  // CATÁLOGO DE COMANDOS
  // ==============================

  loadCommands(): void {

    this.zeroUiApi
      .getCommands()
      .subscribe({

        next: (commands) => {

          this.commands.set(commands);

        },

        error: () => {

          this.commands.set(null);

        }

      });

  }


  // ==============================
  // SUSPENDER ZEROUI
  // ==============================

  suspendZeroUi(): void {

    this.actionLoading.set(true);

    this.actionMessage.set('');

    this.zeroUiApi
      .suspendSystem()
      .subscribe({

        next: () => {

          this.actionMessage.set(
            'ZeroUI suspendido correctamente.'
          );

          this.actionLoading.set(false);

          this.refreshDashboard(false);

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo suspender ZeroUI.'
          );

          this.actionLoading.set(false);

        }

      });

  }


  // ==============================
  // ACTIVAR ZEROUI
  // ==============================

  activateZeroUi(): void {

    this.actionLoading.set(true);

    this.actionMessage.set('');

    this.zeroUiApi
      .activateSystem()
      .subscribe({

        next: () => {

          this.actionMessage.set(
            'ZeroUI activado correctamente.'
          );

          this.actionLoading.set(false);

          this.refreshDashboard(false);

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo activar ZeroUI.'
          );

          this.actionLoading.set(false);

        }

      });

  }


  // ==============================
  // MOSTRAR COMANDOS
  // ==============================

  showCommands(): void {

    this.actionLoading.set(true);

    this.actionMessage.set('');

    this.zeroUiApi
      .showCommands()
      .subscribe({

        next: () => {

          this.actionMessage.set(
            'Panel de comandos mostrado.'
          );

          this.actionLoading.set(false);

          this.refreshDashboard(false);

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo mostrar el panel.'
          );

          this.actionLoading.set(false);

        }

      });

  }


  // ==============================
  // OCULTAR COMANDOS
  // ==============================

  hideCommands(): void {

    this.actionLoading.set(true);

    this.actionMessage.set('');

    this.zeroUiApi
      .hideCommands()
      .subscribe({

        next: () => {

          this.actionMessage.set(
            'Panel de comandos ocultado.'
          );

          this.actionLoading.set(false);

          this.refreshDashboard(false);

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo ocultar el panel.'
          );

          this.actionLoading.set(false);

        }

      });

  }


  // ==============================
  // FORMATO DE DURACIÓN
  // ==============================

  formatDuration(
    seconds: number
  ): string {

    const totalSeconds =
      Math.floor(seconds);

    const minutes =
      Math.floor(
        totalSeconds / 60
      );

    const remainingSeconds =
      totalSeconds % 60;

    return (
      String(minutes).padStart(2, '0')
      + ':'
      + String(remainingSeconds).padStart(2, '0')
    );

  }

}