import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as DistanceIcon} from 'corefacility-base/shared-view/icons/distance.svg';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';


/**
 * 	Allows the user to calculate the distance to the nearest pinwheel center
 */
export default class PinwheelDistanceTool extends BaseTool{

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Calculate the distance map");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <DistanceIcon/>;
	}

	/**
	 * 	Triggers when the user chooses a given tool
	 */
	selectTool(drawer){
		if (drawer.props.onPinwheelDistance){
			drawer.props.onPinwheelDistance();
		}
		return true;
	}

}