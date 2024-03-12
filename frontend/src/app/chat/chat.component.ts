import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../environment';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  userPrompt: string = '';
  modelResponse: string = '';
  backendServerURL = `http://${environment.backendServerHost}:${environment.backendServerPort}/graphql`;

  constructor(private http: HttpClient) { }

  chatModelQuery(text: string) {
    const query = `
      query Chat($message: String!) {
        chat(message: $message)
      }
    `;

    const variables = {
      message: text
    };

    // Using HttpClient to send a GraphQL request
    this.http.post(this.backendServerURL, {
      query: query,
      variables: variables
    }).subscribe({
      next: (response: any) => {
        console.log('API Response:', response);
        // Update the modelResponse with the data received from the server
        // Adjust the path according to your server response structure
        this.modelResponse = response.data.chat;
      },
      error: (error) => {
        console.error('Error:', error);
      }
    });
  }
}
