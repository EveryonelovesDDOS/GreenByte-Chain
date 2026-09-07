import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { sepolia } from 'wagmi/chains';

export const config = getDefaultConfig({
  appName: 'GreenByte Hackathon Project',
  projectId: '123456', 
  chains: [
    sepolia, 
  ],
  ssr: true,
});