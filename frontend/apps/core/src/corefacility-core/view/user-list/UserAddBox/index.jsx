import {translate as t} from 'corefacility-base/utils';
import User from 'corefacility-base/model/entity/User';
import CreateForm from 'corefacility-base/view/CreateForm';
import DialogBox from 'corefacility-base/shared-view/components/DialogBox';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import Label from 'corefacility-base/shared-view/components/Label';

import styles from './style.module.css';



/** User add dialog box */
export default class UserAddBox extends CreateForm{

	/** Describes all fields that can be filled during the user creation
	 * 	and provides their corresponding values
	 */
	async getDefaultValues(){
		return {
			"login": null,
			"name": null,
			"surname": null,
			"email": null,
			"phone": null,
		}
	}

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return User;
	}

	render(){
		return (
		<DialogBox {...this.getDialogProps()} title={t("Add User")}>
			{ this.renderSystemMessage() }
			<div className={styles.fields}>
				<Label>{t('Login') + " *"}</Label>
				<TextInput
					{...this.getFieldProps('login')}
					htmlType="text"
					tooltip={t("The login is required for the user identification process during authentication")}
					maxLength={100}
				/>
				<Label>{t('First name')}</Label>
				<TextInput
					{...this.getFieldProps('name')}
					htmlType="text"
					tooltip={t("The first name is required for better visualization")}
				/>
				<Label>{t('Last name')}</Label>
				<TextInput
					{...this.getFieldProps('surname')}
					htmlType="text"
					tooltip={t("The last name is required for better visualization")}
				/>
				<Label>{t('E-mail')}</Label>
				<TextInput
					{...this.getFieldProps('email')}
					htmlType="email"
					tooltip={t("The e-mail will be used for password recovery service and sending another notifications")}
				/>
				<Label>{t('Phone number')}</Label>
				<TextInput
					{...this.getFieldProps('phone')}
					htmlType="phone"
					tooltip={t("When suspicious activity was detected, please, call the user using this phone number: the user can confirm or deny this operation")}
				/>
			</div>
			<div className={styles.controls}>
				<PrimaryButton {...this.getSubmitProps()} >
					{t('Add')}
				</PrimaryButton>
				<PrimaryButton type="cancel" onClick={ event => this.dialog.closeDialog(false) } inactive={this.state.inactive}>
					{t('Cancel')}
				</PrimaryButton>
			</div>
		</DialogBox>
		);
	}

}