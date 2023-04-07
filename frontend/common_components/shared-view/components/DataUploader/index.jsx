import {translate as t} from 'corefacility-base/utils';
import FileUploader from 'corefacility-base/view/FileUploader';
import Label from 'corefacility-base/shared-view/components/Label';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as CopyIcon} from 'corefacility-base/shared-view/icons/content-copy.svg';
import {ReactComponent as UploadIcon} from 'corefacility-base/shared-view/icons/upload.svg';
import {ReactComponent as DeleteIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import style from './style.module.css';


/** Provides uploading of the functional map
 * 
 * The file uploader can work in two modes: 
 * 		Controllable mode - the widget is fully controlled by the parent.
 * 		Uncontrollable mode - the widget has its own internal state and doesn't
 * 							control by the parent.
 * 
 * Props:
 * ---------------------------------------------------------------------------------------------------------------------
 * @param {callback} 				onFileSelect		Triggers when the user selects certain file.
 * @param {callback} 				onFileRemove		Triggers when the user clears certain file.
 * @param {callback} 				onError 			Triggers when file upload or delete raises an error.
 * @param {File|string|null} 		value 				If this prop is given, the widget is stated to
 * 														be in controllable mode. This props reflects the
 * 														value of the widget.
 * 														If this prop is omitted, the widget is stated to be in
 * 														uncontrollable mode.
 * @param {File|string} 			defaultValue		In uncontrollable mode defines value of the widget
 * 														after its first mounting.
 * @param {string} 					tooltip				The widget's tooltip.
 * @param {FileManager} 			fileManager			if this parameter was set, the following will happened:
 * 			(a) onFileSelect prop will be ignored, FileManagers's upload() method will be called instead
 *			(b) onFileRemove prop will be ignored, FileManager's delete() method will be called instead
 * 			(c) value prop will be ignored, FileManager's value property will be used instead
 * 				when the FileManager is in progress
 * 			(d) disabled is always treated as false, inactive is always treated as true
 * @param {boolean} 				inactive			If true, the user can't change value of this widget
 * @param {boolean} 				loading 			If inactive is true, prints the 'Loading...' message below the
 * 														uploader. Otherwise, does nothing.
 * @param {boolean} 				readonly 			When the widget is read-only, "Upload" and "Delete" buttons are
 * 														not shown.
 * 
 * State:
 * ---------------------------------------------------------------------------------------------------------------------
 * @param {File|string|null} 		value 				Value of the widget in uncontrollable mode.
 * 														Value of this state is useless in controllable mode.
 * @param {boolean} 				disabled			If true, the user can't change the value of this widget and
 * 														all controls look to be disabled.
 * @param {boolean} 				inactive			if true, the user can't change value of this widget. inactive is
 * 														true if either inactive state or inactive prop is true
 * @param {boolean} 				loading 			If inactive is true, prints the 'Loading...' message below the
 * 														uploader. Otherwise, does nothing.
 * 
 * Types of values:
 * 		File - the local client's file opened in the Web browser but still not uploaded.
 * 		string - the URL to the file that has already been uploaded to the Web server.
 * 		null - means that the widget contains no file.
 * 
 * Use the following values for the value state and value and defaultValue props:
 * 		1) when the file is available on the client (has not been uploaded), use File object
 * 		2) when the file is available on the server (has been uploaded) use string
 * 		3) when no file is attached, use null
 */
export default class DataUploader extends FileUploader{

	constructor(props){
		super(props);
		this.handleCopy = this.handleCopy.bind(this);
	}

	/**
	 *  Human-readable description of the widget value
	 */
	get valueDescription(){
		if (this.value instanceof File){
			return this.value.name;
		} else {
			return this.value;
		}
	}

	renderContent(){
		let iconProps = {
			type: 'mini',
			inactive: this.loading || this.inactive || this.disabled,
			disabled: this.disabled,
		}

		return [
			<Label>{t("Please, select a file to upload")}</Label>,
			<div className={style.uploading_pane}>
				<div className={style.filename}>{this.valueDescription}</div>
				{!this.props.readonly && this.value !== null && <Icon
					{...iconProps}
					src={<CopyIcon/>}
					onClick={this.handleCopy}
					tooltip={t("Copy to clipboard")}
				/>}
				{!this.props.readonly && <Icon
					{...iconProps}
					src={<UploadIcon/>}
					onClick={this.handleUpload}
					tooltip={t("Upload")}
					
				/>}
				{this.value !== null && this.props.additionalIcons}
				{!this.props.readonly && this.value !== null && <Icon
					{...iconProps}
					src={<DeleteIcon/>}
					onClick={this.handleRemove}
					tooltip={t("Remove")}
				/>}
			</div>,
			this.inactive && this.loading && <p className={style.message}>{t("Loading...")}</p>,
			this.props.error && <p className={`${style.message} ${style.error}`}>{this.props.error}</p>,
		];
	}

	async handleCopy(event){
		if (!this.valueDescription){
			return;
		}
		await window.navigator.clipboard.writeText(this.valueDescription);		
	}

}