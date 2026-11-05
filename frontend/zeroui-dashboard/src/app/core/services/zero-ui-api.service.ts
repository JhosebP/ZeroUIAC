import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { API_CONFIG } from '../config/api.config';
import { SystemStatus } from '../models/system-status.model';

import {
  AdaptationState
} from '../models/adaptation-state.model';

export interface SystemControlResult {
  success: boolean;
  active: boolean;
  suspended: boolean;
}

export interface CommandsVisibilityResult {
  success: boolean;
  commands_visible: boolean;
}

@Injectable({
  providedIn: 'root'
})
export class ZeroUiApiService {

  constructor(
    private http: HttpClient
  ) {}

  getSystemStatus(): Observable<SystemStatus> {
    return this.http.get<SystemStatus>(
      `${API_CONFIG.baseUrl}/status`
    );
  }

  getAdaptationState(): Observable<AdaptationState> {
    return this.http.get<AdaptationState>(
      `${API_CONFIG.baseUrl}/adaptation`
    );
  }

  suspendSystem(): Observable<SystemControlResult> {
    return this.http.post<SystemControlResult>(
      `${API_CONFIG.baseUrl}/system/suspend`,
      {}
    );
  }

  activateSystem(): Observable<SystemControlResult> {
    return this.http.post<SystemControlResult>(
      `${API_CONFIG.baseUrl}/system/activate`,
      {}
    );
  }

  showCommands(): Observable<CommandsVisibilityResult> {
    return this.http.post<CommandsVisibilityResult>(
      `${API_CONFIG.baseUrl}/commands/show`,
      {}
    );
  }

  hideCommands(): Observable<CommandsVisibilityResult> {
    return this.http.post<CommandsVisibilityResult>(
      `${API_CONFIG.baseUrl}/commands/hide`,
      {}
    );
  }
}