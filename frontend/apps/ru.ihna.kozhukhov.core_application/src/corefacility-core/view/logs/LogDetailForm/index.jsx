import {translate as t} from 'corefacility-base/utils';
import UpdateForm from 'corefacility-base/view/UpdateForm';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import Label from 'corefacility-base/shared-view/components/Label';
import Table from 'corefacility-base/shared-view/components/Table';

import Log from 'corefacility-core/model/entity/Log';

import CoreWindowHeader from '../../base/CoreWindowHeader';
import styles from './style.module.css';


/** Represents log details
 * 
 * 	Such data have the following flow:
 * 
 * 	inputData => defaultValues => rawValues => formValues => formObject => modifyFormObject
 * 
 * 	inputData - a short object that is necessary to build defaultValues.
 * 
 * 	defaultValues - values before the user interactions. These data may
 * 		be downloaded from the external server (in case when user modifies
 * 		the object) or can be simply preliminary set of values (in case
 * 		when user creates new object)
 * 
 * 	rawValues - values entered by the user These values are part of the component
 * 		state: all fields are rendered according to rawValues.
 * 
 * 	formValues - values after primitive proprocessing (i.e., removing loading
 * 		and trailing whitespaces, converting to proper Javascript type, converting
 * 		empty strings to null etc.). These values don't influence on rendering
 * 		of fields.
 * 
 * formObject - strictly must be an instance of Entity.
 * 		On the one hand, formObject is responsible for client-side data validation.
 * 		i.e., it accepts invalidated data from the formValues and must reveal the
 * 		validated data or throw an exception if client-side validation fails.
 * 		On the other side, formObject is the only intermediate that is responsible
 * 		for information exchange between the form and the rest of the world, including
 * 		other components.
 * 
 * 	modifyFormObject - when the formObject is constructedm the modifyFormObject
 * 		becomes the main form function
 * 
 * 
 * 
 * Props:
 * 		@param {object} options		Auxiliary options to be passed to the form.
 * 									They depend on certain subclass specification.
 * 
 * 		@param {object} inputData	When the prop equals to null or undefined,
 * 									the resetForm() method will not be invoked after
 * 									form mounting or pressing the Reload button from
 * 									the main menu. When the prop equals to object,
 * 									the resetForm() will be invoked during the mount
 * 									or press the reload() button and these input data
 * 									will be substituted.
 * 
 * 		@param {function} on404		The function will be evoked when the server received
 * 									error 404 during the reload or update.
 * 
 * State:
 * 		@param {object} rawValues	values as they have been entered by the user
 * 
 * 		@param {object} errors 		Field errors. The field error is defined for
 * 			a certain field (e.g., Incorrect e-mail, phone is not filled etc.).
 * 			This state has a form key => value where where key is field name and
 * 			value is error message corresponding to it
 * 
 * 		@param {string} globalError The error unrelated to any of the fields
 * 			(e.g., authentication failed, network disconnected etc.)
 * 
 * 		@param {boolean} inactive	When the form interacts with the server
 * 			(e.g., fetches or posts the data) its interaction with the rest of
 * 			the world is also impossible
 *
 * 		@param {string} redirect	if string, the form will be redirect to the React.js
 * 									route pointed out in this property. If null, no redirection
 * 									will be provided.
 */
export default class LogDetailForm extends UpdateForm{

	/** The entity class. The formObject will be exactly an instance of this class.
	 * 	The formObject is implied to be an instance of Entity
	 */
	get entityClass(){
		return Log;
	}

	/** List of all entity fields that is allowed to modify using this form
	 */
	get fieldList(){
		return [
			"ip_address",
			"operation_description",
			"request_date",
			"request_method",
			"response_status",
			"user",
			"log_address",
			"request_body",
			"response_body",
			"records",
		];
	}

	/** Renders the form given that the updating entity was successfully loaded.
	 * 		@return {React.Component} Rendered content.
	 */
	renderContent(){
		let requestTime = this.state.rawValues.request_date ?? new Date(0);
		let user = this.state.rawValues.user;
		let userWidget = null;
		let records = this.state.rawValues.records;
		if (user === null || user === undefined){
			userWidget = <i>{t("anonymous")}</i>;
		} else {
			let userName = null;
			if (user.surname === null || user.name === null){
				userName = user.login;
			} else {
				userName = `${user.surname} ${user.name}`;
			}
			userWidget = <Hyperlink href={`/users/${user.id}/`}>{userName}</Hyperlink>;
		}
		
		return (
			<CoreWindowHeader
				{...this.getMessageBarProps()}
				header={t("Log information")}
				>
					<Scrollable>
						<form className={`${styles.form} window-form`}>
							<section className={styles.general_info}>
								<div className={styles.general_info_section}>
									<h2>{requestTime.toLocaleDateString()}</h2>
									<p>{requestTime.toLocaleTimeString()}</p>
								</div>
								<div className={styles.general_info_section}>
									<h2>{t(this.state.rawValues.operation_description)}</h2>
									{this.state.rawValues.ip_address && <p>IP: {this.state.rawValues.ip_address}</p>}
								</div>
							</section>
							<div className={styles.detailed_info}>
								<section className={styles.input_data}>
									<h2>{t("Input data")}</h2>
									<div className={styles.grid_section}>
										<Label>{t("Request address")}</Label>
										<Label>{this.state.rawValues.log_address}</Label>
										<Label>{t("Request method")}</Label>
										<Label>{this.state.rawValues.request_method}</Label>
										<Label>{t("User")}</Label>
										{userWidget}
										<Label>{t("Request body")}</Label>
										<textarea value={this.state.rawValues.request_body} readonly={true}/>
									</div>
								</section>
								<section className={styles.output_data}>
									<h2>{t("Output data")}</h2>
									<div className={styles.grid_section}>
										<Label>{t("Response status")}</Label>
										<Label>{this.state.rawValues.response_status}</Label>
										<Label>{t("Response body")}</Label>
										<textarea value={this.state.rawValues.response_body} readonly={true}/>
									</div>
								</section>
							</div>
							{records && records.length !== 0 && 
								<section>
									<h2>{t("Log records")}</h2>
									<Table
										columns={[
											t("Record date"),
											t("Record time"),
											t("Severity level"),
											t("Message"),
										]}
										data={records.map(record => {
											let recordTime = record.record_time;
											return [
												recordTime.toLocaleDateString(),
												`${recordTime.toLocaleTimeString()}.${recordTime.getMilliseconds()}`,
												record.level.toUpperCase(),
												record.message
													.split("\n")
													.map(messageLine => {
														return <div>{messageLine}</div>;
													}),
											];
										})}
									/>
								</section>
							}
						</form>
					</Scrollable>
			</CoreWindowHeader>
		);
	}

}