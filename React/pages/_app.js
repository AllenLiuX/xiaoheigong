import 'bootstrap/dist/css/bootstrap.min.css';
import '../public/static/styles.css'
import Header from '../components/layouts/Header';

function MyApp({ Component, pageProps }) {
	return (
		<>
			{/* <Header /> */}
			<Component {...pageProps} />
		</>
	)
}

export default MyApp
