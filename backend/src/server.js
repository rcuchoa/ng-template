import { environment } from './environment.js';
import { OpenAI } from 'openai';
import express from 'express';
import { ApolloServer, gql } from 'apollo-server-express';

const production = environment.production;
const debug = environment.debug;
const port = environment.backendServerPort;

// Initialize OpenAI API client
const openai = new OpenAI();

// GraphQL schema definition
const typeDefs = gql`
  type Query {
    chat(message: String!): String!
  }
`;

// GraphQL resolver
const resolvers = {
  Query: {
    chat: async (_, { message }) => {
      try {
        if (debug) { console.log("DEBUG: message: ", message); }

        // Call the OpenAI API to generate completion
        const completion = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          response_format: { type: "text" },
          messages: [
            {
              role: "system",
              content: "You are a helpful assistant designed to output a single text response.",
            },
            { 
              role: "user", 
              content: message 
            }
          ]
        });

        if (debug) { console.log("DEBUG: completion: ", completion); }
        
        // Return the completion text
        return completion.choices[0].message.content;
        
      } catch (error) {
        console.error('Error:', error);
        throw new Error('An error occurred');
      }
    },
  },
};

// Initialize Express server
const app = express();

// Create Apollo Server
const server = new ApolloServer({ typeDefs, resolvers });

// Apply middleware to the Express server
server.start().then(() => {
  server.applyMiddleware({ app });
  
  app.listen(port, () => {
    console.log(`🚀 Server is running on http://localhost:${port}${server.graphqlPath}`);
    if (debug) { console.log("DEBUG: Apollo Server: ", server); }
  });
});
