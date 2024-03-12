export interface EnderecoCompleto {
    rua: string;
    numero: string;
    bairro: string;
    cidade: string;
    estado: string;
    cep: string;
}

export interface NomeCompleto {
    primeiro: string;
    sobrenome: string;
}

export interface EntradaCompleta{
    nome: NomeCompleto;
    endereco: EnderecoCompleto;
}
