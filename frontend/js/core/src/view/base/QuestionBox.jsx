import {translate as t} from '../../utils.mjs';
import Form from './Form.jsx';
import DialogBox from './DialogBox.jsx';
import PrimaryButton from './PrimaryButton.jsx';
import styled from 'styled-components';


/** Represents two-button question box. When the user
 * 	presses Yes, the dialog opening promise always resolves.
 * 	When the user presses No, the dialog opening promise always
 * 	rejects.
 */
export default class QuestionBox extends Form{

	/** Return default values. The function is required if you want the resetForm to work correctly
	 * 	Each field must be mentioned!
	 * 	@async
	 * 		@param {object} inputData some input data passed to the form (They could be undefined)
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		return {...inputData};
	}

	render(){
		let formValues = this._formValues === null ? {} : this._formValues;

		let Message = styled.p`
			margin:  0;
			margin-bottom: 20px;
			padding: 0;
			width: 400px;
		`;

		let ControlBox = styled.div`
			display: flex;
			justify-content: center;
			gap: 30px;
		`;

		return (
			<form>
				<DialogBox {...this.getDialogProps()} title={formValues.caption}>
					<div class="container">
						<Message>{formValues.prompt}</Message>
						<ControlBox>
							<PrimaryButton onClick={event => this.dialog.closeDialog(true)}>{t("Yes")}</PrimaryButton>
							<PrimaryButton onClick={event => this.dialog.closeDialog(false)}>{t("No")}</PrimaryButton>
						</ControlBox>
					</div>
				</DialogBox>
			</form>
		);
	}

}