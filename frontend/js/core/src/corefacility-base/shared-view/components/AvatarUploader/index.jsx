import {translate as t} from 'corefacility-base/utils';
import FileUploader from 'corefacility-base/view/FileUploader';

import Hyperlink from '../Hyperlink';
import styles from './style.module.css';


/** Base class for all widgets that can upload or delete the file.
 * 
 * The file uploader can work in two modes: 
 * 		Controllable mode - the widget is fully controlled by the parent.
 * 		Uncontrollable mode - the widget has its own internal state and doesn't
 * 							control by the parent.
 * 
 * Props:
 * @param {callback} onFileSelect		Triggers when the user selects certain file.
 * @param {callback} onFileRemove		Triggers when the user clears certain file.
 * @param {callback} onError 			Triggers when file upload or delete raises an error.
 * @param {File|string|null} value 		If this prop is given, the widget is stated to
 * 										be in controllable mode. This props reflects the
 * 										value of the widget.
 * 										If this prop is omitted, the widget is stated to be in
 * 										uncontrollable mode.
 * @param {File|string} defaultValue	In uncontrollable mode defines value of the widget
 * 										after its first mounting.
 * @param {string} tooltip				The widget's tooltip.
 * @param {FileManager} fileManager		if this parameter was set, the following will happened:
 * 			onFileSelect prop will be ignored, FileManagers's upload() method will be called instead
 *			onFileRemove prop will be ignored, FileManager's delete() method will be called instead
 * 			value prop will be ignored, FileManager's value property will be used instead
 * 			when the FileManager is in progress, disabled is always treated as false, inactive is always
 * 			treated as true
 * @param {boolean} inactive			If true, the user can't change value of this widget
 * @param {boolean} loading 			If inactive is true, prints the 'Loading...' message below the uploader.
 * 										Otherwise, does nothing.
 * @param {boolean} readonly 			When the widget is read-only, "Upload" and "Delete" buttons are not shown.
 * @param {Number} width 				image width in px
 * @param {Number} height 				image height in px
 * 
 * State:
 * @param {File|string|null} value 		Value of the widget in uncontrollable mode.
 * 										Value of this state is useless in controllable mode.
 * 
 */
 export default class AvatarUploader extends FileUploader{

 	/** Renders internal content of the widget */
	renderContent(){
		let valueWidget = null;
		if (this.valueUrl){
			valueWidget = <img
				className={styles.image_container}
				src={this.valueUrl}
				width={this.props.width}
				height={this.props.height}
				/>;
		} else {
			valueWidget = <div className={`${styles.image_container} ${styles.no_image}`} style={{
				width: `${this.props.width}px`,
				height: `${this.props.height}px`,
			}}></div>;
		}

		let controlsWidget = null;
		if (!this.props.readonly){
			controlsWidget = (
				<div className={styles.controls}>
					<Hyperlink onClick={this.handleUpload} disabled={this.props.disabled} inactive={this.inactive}>{t("Upload")}</Hyperlink>
					<Hyperlink onClick={this.handleRemove} disabled={this.props.disabled} inactive={this.inactive}>{t("Delete")}</Hyperlink>
				</div>
			);
		}

		return (
			<div>
				{valueWidget}
				{controlsWidget}
				{this.props.error !== null && <p className={styles.error}>{this.props.error}</p>}
				{this.inactive && this.loading && <p className={styles.loading}>{t("Loading...")}</p>}
			</div>
		);
	}

 }