import {NotImplementedError} from '../../exceptions/model.mjs';
import ListEditor from './ListEditor.jsx';
import PrimaryButton from './PrimaryButton.jsx';
import MessageBar from './MessageBar.jsx';
import styles from '../base-styles/EntityEditor.module.css';



/** This is a base class for user, project and group list editors
 *  styled in the following way:
 * 		- Add entity button is at the top-right corner;
 * 		- The list editor starts from header;
 *      - error / loading / information message is at the top of the editor;
 *      - list of entities satisfying given conditions is below
 */
export default class CoreListEditor extends ListEditor{

	/** Name of the button that adds new entity */
	get addItemButtonName(){
		throw new NotImplementedError("get addItemButtonName");
	}

	/** Name of the list that will be printed above all */
	get listHeader(){
		throw new NotImplementedError("get listHeader");
	}

	/** Renders the "Add new Entity" button.
	 *  Redeclare this method if you want to do it in another way
	 * 
	 * 	@return {React.Component}
	 */
	renderAddButton(){
		return (<PrimaryButton onClick={this.handleAddButton} type="submit" inactive={this.isLoading}>
			{ this.addItemButtonName }
		</PrimaryButton>);
	}

	render(){
		let pendingClass = (this.isLoading || this.isError) ? styles.pending : null;

		return (
		    <div className={styles.primary}>
				<aside>
					{ this.renderAddButton() }
				</aside>
				<h1>{ this.listHeader }</h1>
				<MessageBar
					isLoading={this.isLoading}
					isError={this.isError}
					error={this.error}
					isAnimatable={true}
				/>
				<article className={pendingClass}>
					{ this.renderItemList() }
				</article>
			</div>
		);
	}

}