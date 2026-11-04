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

  loading = signal(false);

  error = signal(false);

  constructor(
    private zeroUiApi: ZeroUiApiService
  ) {}

  ngOnInit(): void {
    this.loadStatus();
  }

  loadStatus(): void {

    console.log(
      '[ZeroUI] Solicitando estado...'
    );

    this.loading.set(true);

    this.error.set(false);

    this.zeroUiApi
      .getSystemStatus()
      .subscribe({

        next: (status) => {

          console.log(
            '[ZeroUI] Estado recibido:',
            status
          );

          this.status.set(status);

          this.loading.set(false);
        },

        error: (error) => {

          console.error(
            '[ZeroUI] Error consultando API:',
            error
          );

          this.status.set(null);

          this.error.set(true);

          this.loading.set(false);
        }

      });
  }
}