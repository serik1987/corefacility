/** Defines the entity state.
 *  Detailed description of the entity state is given in the Entity help
 */
let EntityState = {
	creating: 'creating',
	pending: 'pending',
	saved: 'saved',
	loaded: 'loaded',
	changed: 'changed',
	deleted: 'deleted',
	found: 'found',
};

Object.freeze(EntityState);

export default EntityState;