curl -g -S -s `
-X POST `
-H "Content-Type: application/json" `
-H "Authorization: JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6IkphbmEiLCJleHAiOjE2NDA1MjI3MjYsIm9yaWdJYXQiOjE2NDA1MjI0MjZ9.LqGB89uoN6SxrizzKVdGeuB6GYut_2utk8hpb9jmFmk" `
-d `@query.graphql `
http://localhost:8000/graphql/