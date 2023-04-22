import {translate as t} from 'corefacility-base/utils';
import UpdateForm from 'corefacility-base/view/UpdateForm';
import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import RectangularRoi from 'corefacility-roi/model/RectangularRoi';

import style from './style.module.css';


export default class RectangularRoiForm extends UpdateForm{

	/**
	 * 	Class of the entity to deal with
	 */
	get entityClass(){
		return RectangularRoi;
	}

	/**
	 *  Requests the object from the server
	 * 	@async
	 * 	@param {Any} 	lookup 			The object identity (e,g., ID, alias, ...)
	 * 	@return the object itself
	 */
	async fetchObject(lookup){
		return RectangularRoi.get({parent: window.application.functionalMap, id: lookup});
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return ['left', 'top', 'right', 'bottom'];
	}

	render(){
		return (
			<DialogBox
				{...this.getDialogProps()}
				title={t("ROI properties")}
				cssSuffix={style.dialog}
			>
				{this.renderSystemMessage()}
				{super.render()}
			</DialogBox>
		);
	}


	/** Renders the form given that the updating entity was successfully loaded.
	 * 		@return {React.Component} Rendered content.
	 */
	renderContent(){
		return (
			<form className={style.root}>
				<div className={style.data_block}>
					<Label>{t("Left")}</Label>
					<TextInput {...this.getFieldProps('left')} />
					<Label>{t("Right")}</Label>
					<TextInput {...this.getFieldProps('right')}/>
					<Label>{t("Top")}</Label>
					<TextInput {...this.getFieldProps('top')}/>
					<Label>{t("Bottom")}</Label>
					<TextInput {...this.getFieldProps('bottom')}/>
				</div>
				<div className={style.controls_block}>
					<PrimaryButton {...this.getSubmitProps()}>{t("Continue")}</PrimaryButton>
					<PrimaryButton
						{...this.getSubmitProps()}
						type="cancel"
						onClick={event => this.dialog.closeDialog(false)}
					>
						{t("Cancel")}
					</PrimaryButton>
				</div>
			</form>
		);
	}

}