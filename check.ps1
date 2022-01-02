curl -g -S -s `
-X POST `
-H "Content-Type: application/json" `
-d `@query.graphql `
http://localhost:8000/graphql/