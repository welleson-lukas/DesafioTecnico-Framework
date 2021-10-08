# Desafio Técnico - Framework

## Resumo do projeto

Blog WEB e API usando Flask, PostgreSQL e Docker.


## Informações para Teste

Para utilizar o projeto é necessário executar:

```
# docker-compose up
```



### Cadastrar novos usuários - API
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/user/register` informando usuário, e-mail e senha.
```
{
	"username": "nome_usuario",
	"password": "senha",
	"email": "meu@email.com"
}
```


### Login usuário - API
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/user/login` informando usuário e senha.
```
{
	"username": "nome_usuario",
	"password": "senha"
}
```

### Cadastrar post - AP
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/post` informando título, conteúdo e imagem.
*informar token JWT em authorization, Bearer jwt-token* - **realizar upload usando multipart form**
```
{
	"title": "titulo do post",
	"content": "conteúdo do post",
	"image": "upload com multipart form"
}
```

### Remover post - AP
Utilize o método `DELETE` para a url: `http://127.0.0.1:5000/api/post/<id>` informando id do post.
*informar token JWT em authorization, Bearer jwt-token*

### Comentar post - AP
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/comment` informando comentario e id do post.
*informar token JWT em authorization, Bearer jwt-token*
```
{
	"comment": "Comentário de um post",
	"post_id": 1
}
```

### Remover comentário post - API
Utilize o método `DELETE` para a url: `http://127.0.0.1:5000/api/comment/<id>` informando id do comentário.
*informar token JWT em authorization, Bearer jwt-token*

### Cadastrar álbum - API
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/album` informando título.
*informar token JWT em authorization, Bearer jwt-token*
```
{
	"title": "titulo do post"
}
```

### Remover álbum - API
Utilize o método `DELETE` para a url: `http://127.0.0.1:5000/api/album/<id>` informando id do álbum.
*informar token JWT em authorization, Bearer jwt-token*

### Cadastrar imagem de álbum - API
Utilize o método `POST` para a url: `http://127.0.0.1:5000/api/album/image/create` informando imagem e id álbum.
*informar token JWT em authorization, Bearer jwt-token* - **realizar upload usando multipart form**
```
{
	"image": "upload com multipart form",
	"album_id": 1
}
```

### Remover album - API
Utilize o método `DELETE` para a url: `http://127.0.0.1:5000/api/album/image/<id>` informando id da imagem.
*informar token JWT em authorization, _Bearer jwt-token_*

### Acesso a interface WEB
`http://127.0.0.1:5000/`