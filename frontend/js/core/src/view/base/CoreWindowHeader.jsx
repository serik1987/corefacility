import MessageBar from './MessageBar.jsx';
import styles from '../base-styles/CoreWindowHeader.module.css';


export default function CoreWindowHeader(props){
	const pendingClass = (props.isLoading || props.isError) ? styles.pending : null;

	return (
		<div className={styles.primary}>
			<aside>
				{ props.aside }
			</aside>
			<h1>{ props.header }</h1>
			<MessageBar
				isLoading={props.isLoading}
				isError={props.isError}
				error={props.error}
				isAnimatable={true}
			/>
			<article className={pendingClass}>
				{props.children}
			</article>
		</div>
	);

}