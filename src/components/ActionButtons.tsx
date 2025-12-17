import React from 'react';

export const ActionButtons = ({ chapterId }: { chapterId: string }) => {
  return (
    <div style={{ marginTop: '20px' }}>
      <button onClick={() => personalizeChapter(chapterId)}>Personalize Content</button>
      <button onClick={() => translateChapter(chapterId)}>Translate to Urdu</button>
    </div>
  );
};

// Functions to call API
async function personalizeChapter(chapterId: string) {
  const res = await fetch(`/api/personalize?chapterId=${chapterId}`);
  const data = await res.json();
  alert(`Personalized content: ${data.result}`);
}

async function translateChapter(chapterId: string) {
  const res = await fetch(`/api/translate?chapterId=${chapterId}`);
  const data = await res.json();
  alert(`Urdu translation: ${data.result}`);
}
