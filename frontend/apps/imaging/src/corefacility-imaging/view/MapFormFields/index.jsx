import {translate as t} from 'corefacility-base/utils';

import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import MessageBar from 'corefacility-base/shared-view/components/MessageBar';
import Label from 'corefacility-base/shared-view/components/Label';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import ComboBox from 'corefacility-base/shared-view/components/ComboBox';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';

import style from './style.module.css';


/**
 * 	Draws fields forms that allow to add or change the user data.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {object}				dialogBoxOptions			Props to be inserted to the dialog box,
 * 	@oaram {React.Component} 	messageBar					Message bar to be inserted
 * 	@param {object} 			aliasFieldOptions 			Props to be inserted to the 'alias' field.
 * 	@param {object} 			typeFieldOptions			Props to be inserted to the 'type' field.
 * 	@param {object} 			widthFieldOptions			Props to be inserted to the 'width' field.
 * 	@param {object}				heightFieldOptions 			Props to be inserted to the 'height' field.
 * 	@param {object} 			submitProps 				Props to be inserted to the 'Submit' button.
 * 	@param {object}				cancelProps					Props to be inserted to the 'Cancel' button.
 * 
 * 	The component is fully stateless.
 */
export default function MapFormFields(props){
	let requiredProps=['dialogBoxOptions', 'aliasFieldOptions', 'typeFieldOptions',
		'widthFieldOptions', 'heightFieldOptions', 'submitProps', 'cancelProps'];
	for (let prop of requiredProps){
		if (!(prop in props)){
			throw new Error(`The prop '${prop}' is required for the component MapFormFields`);
		}
	}

	const mapTypes = [
		{
			value: 'ori',
			text: t("Orientation map"),
		},
		{
			value: 'dir',
			text: t("Directional map")
		}
	];

	let form = [
		props.messageBar,
		<form>
			<div className={style.data_block}>
				<Label>{t("Map alias") + ' *'}</Label>
				<TextInput
					{...props.aliasFieldOptions}
					maxLength={50}
					tooltip={t("A short name of the map that participates in URI. Must contain small and capital "
						+ "latin letters, digits, underscores or hypnens")}
				/>
				<Label>{t("Map type")}</Label>
				<ComboBox
					{...props.typeFieldOptions}
					valueList={mapTypes}
				/>
				<Label>{t("Width, um")}</Label>
				<TextInput
					{...props.widthFieldOptions}
				/>
				<Label>{t("Height, um")}</Label>
				<TextInput
					{...props.heightFieldOptions}
				/>
			</div>
			<div className={style.controls_block}>
				<PrimaryButton {...props.submitProps}>{t("Continue")}</PrimaryButton>
				<PrimaryButton type="cancel" {...props.cancelProps}>{t("Cancel")}</PrimaryButton>
			</div>
		</form>
	]

	if (props.dialogBoxOptions){
		return (
			<DialogBox
				{...props.dialogBoxOptions}
				title={t("Functional map properties")}
			>
				{form}	
			</DialogBox>
		);
	} else {
		return form;
	}
}
