import {translate as t} from '../../utils.mjs';
import User from '../../model/entity/user.mjs';
import CreateForm from '../base/CreateForm.jsx';
import DialogBox from '../base/DialogBox.jsx';
import TextInput from '../base/TextInput.jsx';
import PrimaryButton from '../base/PrimaryButton.jsx';
import Label from '../base/Label.jsx';
import styles from './UserAddBox.module.css';



/** User add dialog box */
export default class UserAddBox extends CreateForm{

	/** Describes all fields that can be filled during the user creation
	 * 	and provides their corresponding values
	 */
	get defaultValues(){
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
				<PrimaryButton type="submit" onClick={this.handleSubmit} inactive={this.state.inactive} disabled={!this.isSubmittable}>
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