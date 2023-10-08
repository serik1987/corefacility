import {translate as t} from 'corefacility-base/utils';
import PasswordRecoveryAuthorizationModule from 'corefacility-core/model/entity/PasswordRecoveryAuthorizationModule';
import Label from 'corefacility-base/shared-view/components/Label';
import PositiveDurationInput from 'corefacility-base/shared-view/components/PositiveDurationInput';
import ModuleForm from '../ModuleForm';
import style from './style.module.css';


/** Provides setup for the password recovery authorization feature
 */
export default class PasswordRecoveryAuthorizationModuleForm extends ModuleForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return PasswordRecoveryAuthorizationModule;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return ['password_recovery_lifetime'];
	}

	/** Renders all settings for the module widget except Application status -> Enabled checkbox,
	 * 	Save Settings button and 'Settings was not saved' message
	 */
	renderAuxiliarySettings(){
		return [
			<div className={style.activation_code_lifetime_label}>
				<Label>{t("Activation code lifetime")}</Label>
			</div>,
			<div className={style.activation_code_lifetime_widget}>
				<PositiveDurationInput
					{...this.getFieldProps('password_recovery_lifetime')}
					tooltip={t("After this given amount of time the activation code becomes invalid")}
				/>
			</div>
		];
	}

}