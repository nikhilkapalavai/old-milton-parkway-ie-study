import { runExperiment } from './simulation';
self.onmessage = ({ data }) => {
  try {
    self.postMessage({ id: data.id, result: runExperiment(data.settings) });
  } catch (error) {
    self.postMessage({
      id: data.id,
      error:
        error instanceof Error ? error.message : 'Unable to run this scenario.',
    });
  }
};
