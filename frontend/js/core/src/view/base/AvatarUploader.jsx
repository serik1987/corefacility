import {translate as t} from '../../utils.mjs';
import FileUploader from './FileUploader.jsx';
import Hyperlink from './Hyperlink.jsx';
import styles from '../base-styles/AvatarUploader.module.css';


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
 * @param {File|string|null} value 		If this prop is given, the widget is stated to
 * 										be in controllable mode. This props reflects the
 * 										value of the widget.
 * 										If this prop is omitted, the widget is stated to be in
 * 										uncontrollable mode.
 * @param {File|string} defaultValue	In uncontrollable mode defines value of the widget
 * 										after its first mounting.
 * @param {string} error 				The error message that will be printed below the image uploader
 * @param {boolean} disabled			If true, the user can't change the value of this widget and
 * 										all controls look to be disabled
 * @param {boolean} inactive			If true, the user can't change value of this widget
 * @param {boolean} loading 			If inactive is true, prints the 'Loading...' message below the uploader.
 * 										Otherwise, does nothing.
 * @param {Number} width 				image width in px
 * @param {Number} height 				image height in px
 * @param {boolean} readonly 			When the widget is read-only, "Upload" and "Delete" buttons are not shown.
 * 
 * State:
 * @param {File|string|null} value 		Value of the widget in uncontrollable mode.
 * 										Value of this state is useless in controllable mode.
 * 
 */
 export default class AvatarUploader extends FileUploader{

 	/** Renders internal content of the widget */
	renderContent(){
		console.log("Avatar render.");

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