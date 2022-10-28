import {NotImplementedError} from '../../exceptions/model.mjs';
import ListEditor from './ListEditor.jsx';
import PrimaryButton from './PrimaryButton.jsx';
import CoreWindowHeader from './CoreWindowHeader.jsx';




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

	render(){

		return (
			<CoreWindowHeader
				isLoading={this.isLoading}
				isError={this.isError}
				error={this.error}
				header={this.listHeader}
				aside={
					<PrimaryButton onClick={this.handleAddButton} type="submit" inactive={this.isLoading}>
						{ this.addItemButtonName }
					</PrimaryButton>
				}
				>
					{ this.renderItemList() }
			</CoreWindowHeader>
		);

	}

}