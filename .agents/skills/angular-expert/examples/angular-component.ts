/**
 * @file example-component.ts
 * @description Exemplo de estruturação de um componente Angular usando Signals (input/output) e documentação extensa.
 * Este componente deve ser usado como "Espelho" pela IA para padronização de sintaxe e estilo de comentários.
 */

import { Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-example-button',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './example-button.component.html',
  styleUrl: './example-button.component.scss'
})
export class ExampleButtonComponent {
  
  /** 
   * Rótulo (texto) exibido dentro do botão. 
   * É obrigatório para renderização.
   */
  label = input.required<string>();
  
  /** 
   * Variável que define a variante visual do botão. 
   * Padrão: 'primary'
   */
  variant = input<'primary' | 'outline' | 'white'>('primary');
  
  /** 
   * Sinaliza se o botão está desabilitado para cliques.
   */
  isDisabled = input<boolean>(false);

  /** 
   * Evento disparado quando o botão é clicado (caso não esteja desabilitado).
   */
  btnClick = output<void>();

  /**
   * Método executado ao clicar no botão HTML.
   * Valida se o botão não está desabilitado antes de emitir o evento de clique.
   */
  onClick(): void {
    if (!this.isDisabled()) {
      this.btnClick.emit();
    }
  }
}
