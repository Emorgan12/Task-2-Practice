import React from "react";
import Link from "next/link";

const Footer = () => {
    
    return (
        <footer>
            <ul>
                <Link href="https://footprint.wwf.org.uk/" target="_blank"><li>Carbon Footprint Calculator</li></Link>
                <Link href="https://consumption.selectra.co.uk/" target="_blank"><li>Energy Usage Calculator</li></Link>
            </ul>
            <ul>
                <Link href="/privacy-policy"><li>Privacy Policy</li></Link>
                <Link href="/accessibility-statement"><li>Accessibilty Statement</li></Link>
            </ul>
            <ul>
                <li>Contact:</li>
                <li>07777 777777</li>
                <Link href="mailto:support@rolsa.tech"><li>support@rolsa.tech</li></Link>
            </ul>
        </footer>
    );
    }

export default Footer;