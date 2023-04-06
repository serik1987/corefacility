import * as React from 'react';
import {useParams} from 'react-router-dom';


export default function DataSelector(props){
	let {lookup} = useParams();

	return React.cloneElement(props.children, {lookup: parseInt(lookup)});
}