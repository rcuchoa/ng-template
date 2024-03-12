import { Component, Output, EventEmitter } from '@angular/core';
import { NomeCompleto, EnderecoCompleto, EntradaCompleta } from '../entrada';

@Component({
  selector: 'app-form',
  templateUrl: './form.component.html',
  styleUrls: ['./form.component.css'],
})
export class FormComponent {
  primeiroInput: string = '';
  sobrenomeInput: string = '';
  ruaInput: string = '';
  numeroInput: string = '';
  bairroInput: string = '';
  cidadeInput: string = '';
  estadoInput: string = '';
  cepInput: string = '';

  entradaCompleta: EntradaCompleta = {
    nome: {
      primeiro: '',
      sobrenome: '',
    },
    endereco: {
      rua: '',
      numero: '',
      bairro: '',
      cidade: '',
      estado: '',
      cep: '',
    },
  };

  @Output() entradaCompletaOutput = new EventEmitter<EntradaCompleta>();

  onClick(): void {
    console.log('Input value:', this.entradaCompleta);
  }

  enviaEntrada() {
    this.entradaCompleta.nome.primeiro = this.primeiroInput;
    this.entradaCompleta.nome.sobrenome = this.sobrenomeInput;
    this.entradaCompleta.endereco.rua = this.ruaInput;
    this.entradaCompleta.endereco.numero = this.numeroInput;
    this.entradaCompleta.endereco.bairro = this.bairroInput;
    this.entradaCompleta.endereco.cidade = this.cidadeInput;
    this.entradaCompleta.endereco.estado = this.estadoInput;
    this.entradaCompleta.endereco.cep = this.cepInput;
    this.entradaCompletaOutput.emit(this.entradaCompleta);
  }
}
