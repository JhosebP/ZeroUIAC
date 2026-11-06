import {
  Component,
  OnInit,
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
export class HomePage implements OnInit {

  status = signal<SystemStatus | null>(null);

  adaptation = signal<AdaptationState | null>(null);

  session = signal<SessionMetrics | null>(null);

  loading = signal(false);

  error = signal(false);

  actionLoading = signal(false);

  actionMessage = signal('');

  constructor(
    private zeroUiApi: ZeroUiApiService
  ) {}

  ngOnInit(): void {

    this.loadStatus();

    this.loadAdaptation();

    this.loadSession();

  }

  loadStatus(): void {

    this.loading.set(true);

    this.error.set(false);

    this.zeroUiApi
      .getSystemStatus()
      .subscribe({

        next: (status) => {

          this.status.set(status);

          this.loading.set(false);

        },

        error: () => {

          this.status.set(null);

          this.error.set(true);

          this.loading.set(false);

        }

      });

  }

  loadAdaptation(): void {

    this.zeroUiApi
      .getAdaptationState()
      .subscribe({

        next: (adaptation) => {

          this.adaptation.set(adaptation);

        },

        error: () => {

          this.adaptation.set(null);

        }

      });

  }

  refreshDashboard(): void {

    this.loadStatus();

    this.loadAdaptation();

    this.loadSession();

  }

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

          this.loadStatus();

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo suspender ZeroUI.'
          );

          this.actionLoading.set(false);

        }

      });

  }

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

          this.loadStatus();

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo activar ZeroUI.'
          );

          this.actionLoading.set(false);

        }

      });

  }

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

          this.loadStatus();

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo mostrar el panel.'
          );

          this.actionLoading.set(false);

        }

      });

  }

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

          this.loadStatus();

        },

        error: () => {

          this.actionMessage.set(
            'No se pudo ocultar el panel.'
          );

          this.actionLoading.set(false);

        }

      });

  }

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

  formatDuration(
      seconds: number
    ): string {
    
      const totalSeconds =
        Math.floor(seconds);
    
      const minutes =
        Math.floor(totalSeconds / 60);
    
      const remainingSeconds =
        totalSeconds % 60;
    
      return (
        String(minutes).padStart(2, '0')
        + ':'
        + String(remainingSeconds).padStart(2, '0')
      );
    
    }

}