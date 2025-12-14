# Get Started in 60 Seconds

## 1. Start Services

```bash
cd /home/thiru/belly/belly/airflow
docker-compose -f docker-compose.sqlite.yml up -d
sleep 40
```

## 2. Open Airflow UI

**http://localhost:8080**

**Login**: `admin` / `admin123`

## 3. View DAGs

Click **"All"** tab → You should see:
- ✅ `price_prediction_nightly`
- ✅ `stats_computation_24h`

## 4. Monitor Execution

- **Graph View**: See task dependencies
- **Tree View**: See execution history
- **Logs**: Click tasks to see output

## Common Commands

```bash
# Check status
docker ps

# View logs
docker logs belly-airflow-scheduler -f

# Stop services
docker-compose -f docker-compose.sqlite.yml down

# Trigger DAG manually
docker exec belly-airflow-scheduler airflow dags trigger stats_computation_24h
```

## Issues?

- **DAGs not showing?** → Hard refresh (Ctrl+Shift+R)
- **Can't login?** → admin / admin123
- **Webserver down?** → `docker logs belly-airflow-webserver`

## Learn More

- Full docs: [README.md](README.md)
- Testing guide: [TESTING.md](TESTING.md)
