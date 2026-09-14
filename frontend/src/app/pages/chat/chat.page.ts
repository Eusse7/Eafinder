import { DatePipe } from '@angular/common';
import {
  AfterViewChecked,
  Component,
  ElementRef,
  OnDestroy,
  OnInit,
  ViewChild,
  inject,
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Subscription } from 'rxjs';

import { ChatStore } from '../../core/chat.store';

@Component({
  selector: 'app-chat',
  imports: [DatePipe],
  templateUrl: './chat.page.html',
})
export class ChatPage implements OnInit, OnDestroy, AfterViewChecked {
  @ViewChild('scroller') scroller?: ElementRef<HTMLDivElement>;

  protected readonly store = inject(ChatStore);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  private subscription?: Subscription;
  private lastCount = 0;
  /** Artículo cuyo texto literal se está mostrando expandido (US09). */
  protected openSource: string | null = null;

  ngOnInit(): void {
    this.subscription = this.route.paramMap.subscribe(async (params) => {
      const chatId = params.get('chatId');

      if (!chatId) {
        this.router.navigate(['/']);
        return;
      }

      const found = await this.store.loadChat(chatId);

      if (!found) {
        this.router.navigate(['/']);
      }
    });
  }

  ngAfterViewChecked(): void {
    const count = this.store.messages().length;

    if (count !== this.lastCount) {
      this.lastCount = count;
      this.scrollToBottom();
    }
  }

  ngOnDestroy(): void {
    this.subscription?.unsubscribe();
  }

  toggleSource(id: string): void {
    this.openSource = this.openSource === id ? null : id;
  }

  private scrollToBottom(): void {
    const element = this.scroller?.nativeElement;

    if (element) {
      queueMicrotask(() => {
        element.scrollTop = element.scrollHeight;
      });
    }
  }
}
