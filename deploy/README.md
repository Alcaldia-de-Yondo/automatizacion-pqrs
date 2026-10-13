# Despliegue del temporizador PQRSD

Desde la raíz del repositorio, copie el servicio y el temporizador:

```bash
sudo cp deploy/pqrsd.service /etc/systemd/system/
sudo cp deploy/pqrsd.timer /etc/systemd/system/
```

Cree los directorios auxiliares si el proyecto aún no los tiene:

```bash
mkdir -p logs tmp informes
chmod +x scripts/run.sh
```

Recargue `systemd` y active la ejecución periódica:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pqrsd.timer
sudo systemctl start pqrsd.timer
```

Para verificar el estado:

```bash
sudo systemctl status pqrsd.timer
```

Para revisar las últimas ejecuciones:

```bash
tail -f logs/ejecuciones.log
tail -f logs/pqrsd.log
```
