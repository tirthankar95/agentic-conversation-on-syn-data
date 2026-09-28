# Conversational AI on Synthetic Data

## How to run the code 
`Open docker desktop and run postgres`
`streamlit run app.py`


# Accessing tables in database
Refer to app5.py
```sql
docker build -t my-postgres .

docker run -d \
  --name postgres-container \
  -p 5432:5432 \
  my-postgres

docker start postgres-container
docker exec -it postgres-container psql -U myuser -d mydb
```

