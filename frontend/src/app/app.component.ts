import { Component } from '@angular/core';
import { EntradaCompleta } from './entrada';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title: string = 'myapp';

  entrada: EntradaCompleta = {
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

  outputText = '';

  recebeEntrada(data: EntradaCompleta) {
    console.log(data);
    this.entrada.nome.primeiro = data.nome.primeiro;
    this.entrada.nome.sobrenome = data.nome.sobrenome;
    this.entrada.endereco.rua = data.endereco.rua;
    this.entrada.endereco.numero = data.endereco.numero;
    this.entrada.endereco.bairro = data.endereco.bairro;
    this.entrada.endereco.cidade = data.endereco.cidade;
    this.entrada.endereco.estado = data.endereco.estado;
    this.entrada.endereco.cep = data.endereco.cep;
    this.outputText = `Olá ${this.entrada.nome.primeiro} ${this.entrada.nome.sobrenome}! Seu convite será enviado para o endereço: ${this.entrada.endereco.rua}, ${this.entrada.endereco.numero} - ${this.entrada.endereco.bairro}, ${this.entrada.endereco.cidade} - ${this.entrada.endereco.estado} - ${this.entrada.endereco.cep}.`;
    ;
  }
}
