import { getCards, type CardData } from '../utils/getCards';

import Card from './Card';

export default function Cards() {
  const cards = getCards();

  return (
    <div className="grid grid-cols-1 gap-4 overflow-y-auto px-4 pt-8 sm:grid-cols-2">
      {cards.map((card: CardData) => (
        <Card
          key={card.title}
          icon={card.icon}
          title={card.title}
          content={card.content}
          prompt={card.prompt}
        />
      ))}
    </div>
  );
}
