import React from 'react';
import Chatbot from '@site/src/components/Chatbot/Chatbot';

export default function Root({children}) {
  return (
    <>
      {children}
      <Chatbot backendUrl="https://physical-ai-textbook-jade.vercel.app/" />
    </>
  );
}