import {translate as t} from '../../utils.mjs';
import User from '../../model/entity/user.mjs';
import UpdateForm from '../base/UpdateForm.jsx';
import CoreWindowHeader from '../base/CoreWindowHeader.jsx';
import Scrollable from '../base/Scrollable.jsx';
import Label from '../base/Label.jsx';
import TextInput from '../base/TextInput.jsx';
import CheckboxInput from '../base/CheckboxInput.jsx';
import PrimaryButton from '../base/PrimaryButton.jsx';
import AvatarUploader from '../base/AvatarUploader.jsx';
import styles from './UserDetailForm.module.css';


/** The form allows users to change their profile data and system administrators
 * 	to manage single users in the user list.
 */
export default class UserDetailForm extends UpdateForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return User;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return [
			'login',
			'name',
			'surname',
			'email',
			'phone',
			'unix_group',
			'home_dir',
			'is_locked',
			'is_superuser',
		];
	}

	/** Redirection route for "Save and close" and "Close" buttons
	 */
	get entityListRoute(){
		return "/users/";
	}

	/** Asks the user whether he wants to delete the form object
	 */
	async promptDelete(event){
		return await window.application.openModal("question", {
			caption: t("User delete confirmation"),
			prompt: t("This operation will permanently remove the user account, reset all user's membership in groups. ") +
				t("All user's personal files will also be permanently deleted from the cloud storage. ") + 
				t("Are you wish to continue?"),
		});
	}

	renderContent(){
		let unset = <i className={styles.unset}>{t('Not defined.')}</i>;
		let header
		if (this._formValues && (this._formValues.surname || this._formValues.name)){
			header = `${this._formValues.surname || ''} ${this._formValues.name || ''}`;
		} else {
			header = t("User information");
		}

		if (this.props.setBrowserTitle){
			this.props.setBrowserTitle(header);
		}

		return (
			<CoreWindowHeader
				{...this.getMessageBarProps()}
				header={header}
				>
					<Scrollable>
						<form className={`${styles.main} window-form`}>
							<div className={styles.personal_data_row}>
								<section className={styles.personal_data}>
									<h2>{t("Personal Data")}</h2>
									<div className={styles.widgets}>
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
											maxLength={100}
										/>
										<Label>{t('Last name')}</Label>
										<TextInput
											{...this.getFieldProps('surname')}
											htmlType="text"
											tooltip={t("The last name is required for better visualization")}
											maxLength={100}
										/>
										<Label>{t('E-mail')}</Label>
										<TextInput
											{...this.getFieldProps('email')}
											htmlType="email"
											tooltip={t("The e-mail will be used for password recovery service and sending another notifications")}
											maxLength={254}
										/>
										<Label>{t('Phone number')}</Label>
										<TextInput
											{...this.getFieldProps('phone')}
											htmlType="phone"
											tooltip={t("When suspicious activity was detected, please, call the user using this phone number: the user can confirm or deny this operation")}
											maxLength={20}
										/>
										<Label>{t('UNIX account name')}</Label>
										<Label>{this.state.rawValues.unix_group || unset}</Label>
										<Label>{t('Home directory')}</Label>
										<Label>{this.state.rawValues.home_dir || unset}</Label>
									</div>
								</section>
								<section className={styles.avatar_box}>
									<h2>{t("Avatar")}</h2>
									<AvatarUploader
										{...this.getChildComponentProps("avatar")}
										fileManager={this._formObject && this._formObject.avatar}
										tooltip={t("The user photo facilitates distinguising users among each other. This is not necessary to use your real photo.")}
										width={150}
										height={150}
									/>
								</section>
							</div>
							<div className={styles.administration_row}>
								<section className={styles.password_changer}>
									<h2>{t("User's password")}</h2>
									<p>Layouting Password change...</p>
								</section>
								<section className={styles.administration}>
									<h2>{t("Administration")}</h2>
									<CheckboxInput
										{...this.getFieldProps('is_locked')}
										label={t("Locked")}
										tooltip={t("The user can't authorize when he's locked.")}
									/>
									<CheckboxInput
										{...this.getFieldProps('is_superuser')}
										label={t("Superuser")}
										tooltip={t("Superuser has full access data and features in corefacility as well as in every its application")}
									/>
								</section>
							</div>
							<div className={styles.controls_row}>
								<PrimaryButton {...this.getSubmitProps()}>{t('Save')}</PrimaryButton>
								<PrimaryButton {...this.getSubmitProps()} onClick={this.handleSubmitAndClose}>{t('Save and close')}</PrimaryButton>
								<PrimaryButton
									type="cancel"
									inactive={this.state.inactive}
									onClick={this.handleClose}
									>
										{t('Close without save')}
								</PrimaryButton>
								<PrimaryButton
									type="remove"
									inactove={this.state.inactive}
									onClick={this.handleDelete}
									>
										{t('Remove')}
								</PrimaryButton>
							</div>
						</form>
					</Scrollable>
			</CoreWindowHeader>
		);
	}

}