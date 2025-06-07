import express from 'express';

const PORT = process.env.PORT || 3000;

const app = express();
app.use(express.json()); 

app.get('/health', (req, res) => {
  res.status(200).send('OK');
});

app.post('/events', (req, res) => {
  const event = req.body;

  console.log('Event-Endpunkt aufgerufen (MVP). Event empfangen:', event);

  if (!event || Object.keys(event).length === 0) {
    return res.status(400).send({ message: 'Event-Payload darf nicht leer sein.' });
  }

  res.status(200).send({
    message: 'Event empfangen (MVP - wird noch nicht an Kafka gesendet).',
    receivedEvent: event
  });
});

const server = app.listen(PORT, () => {
  console.log(`http server started on http://localhost:${PORT}`);
});

const gracefulShutdown = () => {
  console.log('Fahre Server herunter...');
  server.close(() => {
    console.log('Server beendet.');
    process.exit(0);
  });
};

process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);