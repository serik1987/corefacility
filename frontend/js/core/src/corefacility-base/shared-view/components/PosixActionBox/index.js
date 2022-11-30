import * as React from 'react';

import {translate as t} from 'corefacility-base/utils';
import Form from 'corefacility-base/view/Form';
import {ReactComponent as ContentCopy} from 'corefacility-base/shared-view/icons/content-copy.svg';

import DialogBox from '../DialogBox';
import Icon from '../Icon';
import PrimaryButton from '../PrimaryButton';
import styles from './style.module.css';


/** Suggests the user to complete some posix action to continue
 * 	the operation. Crucial for the PartServerConfiguration only.
 */
export default class PosixActionBox extends Form{

	constructor(props){
		super(props);
		this.handleCopy = this.handleCopy.bind(this);
		this.__ref = React.createRef();
	}

	/** Returns values that will be immediately inserted into the form
	 * 	@async
	 * 		@param {object} inputData that contains message string and bashCode array
	 * 		@return {object} the defaultValues
	 */
	async getDefaultValues(inputData){
		return {...inputData};
	}

	/** Handles press on the copy button */
	handleCopy(event){
		let textArea = this.__ref.current;
		textArea.select();
		window.document.execCommand("copy");
	}

	render(){
		let bashScript = this.state.rawValues.bashScript && this.state.rawValues.bashScript.join("\n");

		return (
			<DialogBox {...this.getDialogProps()} title={t("Action Required")}>
				<div class={styles.container}>
					<p className={styles.message}>{this.state.rawValues.message}</p>
					<div className={styles.code_wrapper}>
						<textarea
							className={styles.code}
							ref={this.__ref}
							value={bashScript}
						/>
						<Icon
							onClick={this.handleCopy}
							src={<ContentCopy/>}
							tooltip={t("Copy to clipboard")}
						/>
					</div>
					<div className={styles.controls}>
						<PrimaryButton type="submit" onClick={event => this.dialog.closeDialog(true)} inactive={this.state.inactive}>
							{t("Continue")}
						</PrimaryButton>
						<PrimaryButton type="cancel" onClick={event => this.dialog.closeDialog(false)} inactive={this.state.inactive}>
							{t("Cancel")}
						</PrimaryButton>
					</div>
				</div>
			</DialogBox>
		);
	}

}