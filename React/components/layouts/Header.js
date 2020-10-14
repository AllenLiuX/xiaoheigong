import Head from 'next/head';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap';

const Header = () => (
    <div style={{
        marginBottom: '5%'
    }}>
        <Head>
            <title>Report Collector</title>
            <link rel="icon" href="/favicon.ico" />
        </Head>
        <Navbar fixed="top" collapseOnSelect expand="lg" bg="dark" variant="dark">
            <Navbar.Brand href="/">Report Collector</Navbar.Brand>
            <Navbar.Toggle aria-controls="responsive-navbar-nav" />
            <Navbar.Collapse id="responsive-navbar-nav">
                <Nav>
                    <NavDropdown title="pages" id="collasible-nav-dropdown">
                        <NavDropdown.Item href="/page1">page1</NavDropdown.Item>
                        <NavDropdown.Divider />
                        <NavDropdown.Item href="/page2">page2</NavDropdown.Item>
                    </NavDropdown>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    </div>
);

export default Header;