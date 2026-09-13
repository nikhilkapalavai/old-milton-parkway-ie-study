import { createRoot } from 'react-dom/client';
import TrafficLab from './components/traffic-lab';
import './app/globals.css';
import './pages.css';

createRoot(document.getElementById('root')!).render(<TrafficLab />);
