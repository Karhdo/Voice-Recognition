# Voice Recognition

<!-- ABOUT THE PROJECT -->

## About The Project

-   ...

## Build With

-   ...

## Installation

1. Python: version over 3.8
2. Install required libraries in [requirement.txt](https://github.com/Karhdo/Voice-Recognition/blob/86ae116bba8478a737743b05015b479a79948fc0/requirements.txt)

```bash
# install library


# create file .env and add content below
DATABASE_URL="postgresql://postgres:(your_postgre_password)@localhost:5432/ToDoApp?schema=public"

PORT=5000

ACCESS_TOKEN_SECRET=123123123asdasd
REFRESH_TOKEN_SECRET=324sfasddasdasd

# migrate db to postgre server
npx prisma migrate dev --name init

# run server
npm run start
```
