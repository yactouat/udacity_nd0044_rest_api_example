# Backend - REST API

<!-- TOC -->

- [Backend - REST API](#backend---rest-api)
    - [What is this ?](#what-is-this-)
    - [Setting up the Backend](#setting-up-the-backend)
        - [How to run](#how-to-run)
            - [Key Pip Dependencies](#key-pip-dependencies)
        - [How to test](#how-to-test)
        - [API Reference](#api-reference)
            - [General](#general)
            - [Authentication / Authorization](#authentication--authorization)
            - [Error Handling](#error-handling)
            - [Endpoints](#endpoints)
                - [GET /api](#get-api)
                - [GET /api/categories](#get-apicategories)
                - [GET /api/items](#get-apiitems)
                - [POST /api/items](#post-apiitems)
                - [POST /api/stuff](#post-apistuff)
                - [DELETE /api/items/{book_id}](#delete-apiitemsbook_id)

<!-- /TOC -->

## What is this ?

This is a template app' to get a hang at REST APIs with Flask developed in TDD mode. There are 2 main entities in this app':

- `item`
- `category`

There is also a `stuff` endpoint that allows to get random items in a way that previously obtained items dont show if specified.

## Setting up the Backend

### How to run

First, at the root of this `backend` folder, copy the contents of the `.env.example` file to a new `.env` file, if you're running the app' on Docker (which you should), you should be fine with the defaults of the example file !

After that, all you need is a standard install of Docker Desktop, just hit `docker compose up` at the root of this `backend` folder and you're good to go !  
The application stack contains:

- the Python REST app, with all its dependencies (in `requirements.txt`) installed
- one already seeded PostgreSQL instance
- one already seeded test PostgreSQL instance
- one `pgadmin` instance, accessible on `http://localhost:8080` (credentials are in the `docker-compose.yml`)

#### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

### How to test

- run the application stack with a `docker compose up` if it's not already running
- `docker exec -t udacity_nd0044_rest_api_example-python-1 bash -c "python test_flaskr.py"`

### API Reference

#### General

The REST API is a public JSON web API; its response messages, errors or not, will always have this structure:

```json
{
    "msg": "some msg",
    "success": true,
    "data": null
}
```

At the moment this app can only be run locally and is not hosted. So the base URL is `http://localhost/api` after having run `docker compose up` from the root folder.

#### Authentication / Authorization

This version of the application does not require authentication or API keys.

#### Error Handling

The API will those error types when requests fail:

- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable
- 500: Server Error

#### Endpoints

##### GET /api

Ping endpoint to check if API is up. Expected response body payload:

```json
{
    "msg": "REST API is up",
    "success": true,
    "data": null
}
```

##### GET /api/categories

Gets the existing items categories. Expected response body payload is:

```json
{
    "msg": "fetched categories",
    "success": true,
    "data": [
        {
            "id": 1,
            "type": "Science"
        },
        {
            "id": 2,
            "type": "History"
        }
    ]
}
```

##### GET /api/items

Expected response body payload:

```json
{
    "msg": "fetched items",
    "success": true,
    "data": [
        {
            "id": 1,
            "item": "created item",
            "category": "some category"
        },
        {
            "id": 2,
            "item": "created item",
            "category": "some category"
        }
    ]
}
```

This route can take these 2 **optional** query parameters:

- `categ` (string), the type of the category of items you wish to get
- `searchTerm` (string), a search term within the titles of the existing items; if provided, will return only the items containing that search term

Sample requests:

`curl http://localhost/api/items?categ=some_categ`
`curl http://localhost/api/items?searchTerm=some_search_term`

##### POST /api/items

Creates a new item using the following **required** input parameters:

- `item` (string)
- `category`(int), this uses an existing category id

Returns the newly created item in a formatted API response =>

```json
{
    "msg": "item created",
    "success": true,
    "data": {
        "id": 1,
        "item": "created item",
        "category": "some category"
    }
}
```

Sample request :

`curl http://localhost/api/items -X POST -H "Content-Type: application/json" -d '{"item":"created item", "category": "5"}'`

##### POST /api/stuff

Allows to get the next item in a app pseudo randomizer using the following **required** input parameters:

- `prevItems` (int[]), the previous items ids in the current app pseudo randomizer
- `category`(string), the type of the category of items you wish to get; category can also be the value `all`, which means that there wont be any filtering on the categories in the returned item

Returns the newly created item in a formatted API response =>

```json
{
    "msg": "app item fetched",
    "success": true,
    "data": {
        "id": 1,
        "item": "created item",
        "category": "some category"
    }
}
```

Sample request :

`curl http://localhost/api/stuff -X POST -H "Content-Type: application/json" -d '{"prevItems":[1],"category": "some_categ"}'`

##### DELETE /api/items/{book_id}

Deletes a item using the following **required** URL parameter:

- `id` (int), the id of the item to delete

Response is a 204 and has no content.

Sample request:

`curl -X DELETE http://localhost/api/items/16`
