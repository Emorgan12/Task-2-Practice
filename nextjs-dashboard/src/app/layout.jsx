import './globals.css'
import Footer from './ui/footer';
import Navbar from './ui/navbar';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        {children}
        <Footer />
      </body>
    </html>
  );
}
