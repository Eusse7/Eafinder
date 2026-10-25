import { Component, OnInit, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { firstValueFrom } from 'rxjs';

import { ApiService } from '../../core/api.service';
import { AnalyticsData } from '../../core/models';

/**
 * Panel de analítica de búsquedas (US05).
 * Permite visualizar métricas agregadas de consultas y patrones de uso.
 */
@Component({
  selector: 'app-analytics',
  imports: [RouterLink],
  templateUrl: './analytics.page.html',
})
export class AnalyticsPage implements OnInit {
  private readonly api = inject(ApiService);

  protected readonly loading = signal(true);
  protected readonly data = signal<AnalyticsData | null>(null);
  protected readonly error = signal(false);

  ngOnInit(): void {
    this.loadData();
  }

  async loadData(): Promise<void> {
    this.loading.set(true);
    this.error.set(false);

    try {
      const result = await firstValueFrom(this.api.getAnalytics());
      this.data.set(result);
    } catch {
      this.error.set(true);
    } finally {
      this.loading.set(false);
    }
  }
}
