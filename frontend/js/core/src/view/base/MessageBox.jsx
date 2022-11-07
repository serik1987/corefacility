import styled from 'styled-components';

import Form from './Form.jsx';
import DialogBox from './DialogBox.jsx';
import PrimaryButton from './PrimaryButton.jsx';


/** Displays a simple message box with text and OK button.
 * 
 * 	inputData:
 * 		@param {string} title the dialog title
 * 		@param {string} body the message body
 */
export default class MessageBox extends Form{

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@abstract
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		return {...inputData}
	}

	render(){
		const {title, body} = this.state.rawValues;
		const Message = styled.p`
			margin: 0;
		`;
		const Controls = styled.div`
			display: flex;
			justify-content:  center;
		`;

		return (
			<DialogBox
				{...this.getDialogProps()}
				title={title}
				>
					<Message>{body}</Message>
					<Controls>
						<PrimaryButton
							onClick={event => this.dialog.closeDialog(true)}
							inactive={this.state.inactive}
							>
								OK
						</PrimaryButton>
					</Controls>
			</DialogBox>
		);
	}

}