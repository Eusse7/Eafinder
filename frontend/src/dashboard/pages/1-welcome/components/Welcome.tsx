import Cards from './Cards';
import Footer from './Footer';
import Header from './Header';

export default function Welcome() {
  return (
    <div className="flex flex-col items-center text-black">
      <Header />
      <Cards />
      <Footer />
    </div>
  );
}
