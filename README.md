# math-question-analyzer

Work In Progress

## start 

start neo4j by docker
```bash
docker-compose up -d
```
check neo4j
```bash
docker ps
```

start backend 
```bash
cd backend
uvicorn main:app --reload
```

start frontend
```bash
cd frontend
streamlit run app.py
```


## check neo4j via neo4j browser
1. go to browser:  http://localhost:7474

2. Login credentials (from docker-compose.yml):
  - Username: neo4j
  - Password: your_password_here

  (Username and password in demo are neo4j and your_password_here. )
3. Check data in neo4j
  In browser http://localhost:7474
```
  MATCH (n) RETURN count(n);
```
  Create a test node
```
  CREATE (q:Question {text: "What is 2 + 2?"})
  RETURN q;
```
  Verify it was created
  ```
  MATCH (q:Question)
  RETURN q;
  ```
4. Check if Neo4j ports are listening
In terminal
```bash
Test-NetConnection -ComputerName localhost -Port 7474  # Browser interface
Test-NetConnection -ComputerName localhost -Port 7687  # Bolt protocol
```
5. Check math questions loaded in neo4j

```
MATCH p=(q1:Question)-[*1..4]-(q2:Question) RETURN DISTINCT p

```
![{BD074169-E8CE-4F6D-B31B-4E7DDCF592B9}](https://github.com/user-attachments/assets/9ee9c599-67f6-4c29-a1ff-cfad332b2e48)




## log 
### 2025.01.05
Phase 1 start


### 2025.01.18
1. 
format "json-object" is supported by gpt-4o-mini but not gpt-4 
