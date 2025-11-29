"""Groups page component."""
import streamlit as st
import pandas as pd
from datetime import datetime
from app.data import AccountsRepository, GroupsRepository


def render_groups():
    """Render the groups page."""
    accounts_repo = AccountsRepository()
    groups_repo = GroupsRepository()
    
    accounts = accounts_repo.load_all()
    groups = groups_repo.load_all()
    
    st.markdown('<h1 class="hero-title">Your Groups 👥</h1>', unsafe_allow_html=True)
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📋 My Groups", "➕ Create Group", "🔍 Find Groups"])
    
    with tab1:
        user_groups = groups_repo.get_user_groups(st.session_state.user_email)
        
        if user_groups:
            # Search/filter for user's groups
            search_query = st.text_input("🔍 Search your groups", key="my_groups_search", placeholder="Search by name or vibe...")
            
            filtered_groups = user_groups
            if search_query:
                filtered_groups = {
                    name: data for name, data in user_groups.items()
                    if search_query.lower() in name.lower() or search_query.lower() in data.get("vibe", "").lower()
                }
            
            if filtered_groups:
                for group_name, group_data in filtered_groups.items():
                    with st.expander(f"📍 {group_name}", expanded=True):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown(f"**Vibe:** {group_data.get('vibe', 'Casual meetup')}")
                            
                            # Show creator info
                            created_by = group_data.get('created_by', 'Unknown')
                            if created_by in accounts:
                                creator_name = accounts[created_by].get('name', created_by)
                                st.markdown(f"**Created by:** {creator_name}")
                            
                            st.markdown("**Members:**")
                            
                            member_lats = []
                            member_lngs = []
                            
                            # Member management
                            members_list = group_data.get("members", [])
                            is_creator = created_by == st.session_state.user_email
                            
                            for idx, member_email in enumerate(members_list):
                                member = accounts.get(member_email, {})
                                member_name = member.get("name", member_email.split("@")[0])
                                member_addr = member.get("address", "Location not set")
                                lat = member.get("lat")
                                lng = member.get("lng")
                                
                                is_you = member_email == st.session_state.user_email
                                is_member_creator = member_email == created_by
                                
                                # Display member card
                                badges = []
                                if is_you:
                                    badges.append(" (You)")
                                if is_member_creator:
                                    badges.append(" 👑 Creator")
                                
                                col_member, col_action = st.columns([4, 1])
                                with col_member:
                                    st.markdown(f"""
                                    <div class="member-card">
                                        <strong>{member_name}{''.join(badges)}</strong><br>
                                        <small>📍 {member_addr}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                                
                                with col_action:
                                    # Show remove/leave button
                                    if is_you:
                                        # Leave group button
                                        if len(members_list) > 1:
                                            if st.button("Leave", key=f"leave_{group_name}_{idx}", help="Leave this group"):
                                                if st.session_state.get(f"confirm_leave_{group_name}", False):
                                                    groups_repo.remove_member(group_name, member_email)
                                                    st.success(f"You left '{group_name}'")
                                                    st.rerun()
                                                else:
                                                    st.session_state[f"confirm_leave_{group_name}"] = True
                                                    st.warning("⚠️ Click again to confirm")
                                    elif is_creator:
                                        # Creator can remove other members
                                        if st.button("Remove", key=f"remove_{group_name}_{idx}", help="Remove member"):
                                            if st.session_state.get(f"confirm_remove_{group_name}_{idx}", False):
                                                groups_repo.remove_member(group_name, member_email)
                                                st.success(f"Removed {member_name}")
                                                st.rerun()
                                            else:
                                                st.session_state[f"confirm_remove_{group_name}_{idx}"] = True
                                                st.warning("⚠️ Click again to confirm")
                                
                                if lat and lng:
                                    member_lats.append(lat)
                                    member_lngs.append(lng)
                            
                            # Add member button
                            st.markdown("---")
                            available_to_add = [
                                email for email in accounts.keys() 
                                if email not in members_list and email != st.session_state.user_email
                            ]
                            
                            if available_to_add:
                                with st.expander("➕ Add Member"):
                                    selected_new_member = st.selectbox(
                                        "Select member to add",
                                        available_to_add,
                                        key=f"add_member_{group_name}",
                                        format_func=lambda x: f"{accounts[x].get('name', x)} ({x})"
                                    )
                                    if st.button("Add", key=f"add_btn_{group_name}"):
                                        groups_repo.add_member(group_name, selected_new_member)
                                        st.success(f"Added {accounts[selected_new_member].get('name', selected_new_member)} to the group!")
                                        st.rerun()
                        
                        with col2:
                            if member_lats and member_lngs:
                                map_data = pd.DataFrame({
                                    'lat': member_lats,
                                    'lon': member_lngs
                                })
                                st.map(map_data, zoom=11)
                            
                            if st.button(f"📍 Find Meeting Point", key=f"find_{group_name}", use_container_width=True):
                                st.session_state.selected_group = group_name
                                st.session_state.current_page = "find_meeting"
                                st.rerun()
                            
                            # Delete group button (only for creator)
                            if created_by == st.session_state.user_email:
                                st.markdown("---")
                                if st.button(f"🗑️ Delete Group", key=f"delete_{group_name}", use_container_width=True, type="secondary"):
                                    if st.session_state.get(f"confirm_delete_{group_name}", False):
                                        groups_repo.delete(group_name)
                                        st.success(f"Group '{group_name}' deleted")
                                        st.rerun()
                                    else:
                                        st.session_state[f"confirm_delete_{group_name}"] = True
                                        st.error("⚠️ Click again to confirm deletion. This cannot be undone!")
            else:
                st.info("No groups match your search.")
        else:
            st.info("You haven't joined any groups yet. Create one or find an existing group!")
    
    with tab2:
        st.markdown("### Create a New Group")
        
        col1, col2 = st.columns(2)
        with col1:
            new_group_name = st.text_input("Group Name", placeholder="e.g., Weekend Hangout Crew", key="new_group_name")
        with col2:
            new_group_vibe = st.selectbox(
                "What's the vibe?",
                ["☕ Coffee Meetup", "🍽️ Dinner Party", "🎮 Gaming Session", 
                 "📚 Study Group", "🏃 Fitness Buddies", "🎉 Party Time", "💼 Business Meeting", "🌳 Casual Hangout"],
                key="new_group_vibe"
            )
        
        st.markdown("### Add Members")
        st.markdown("*Select members from the community to invite*")
        
        available_members = [email for email in accounts.keys() if email != st.session_state.user_email]
        
        if available_members:
            selected_members = st.multiselect(
                "Select members",
                available_members,
                key="new_group_members",
                format_func=lambda x: f"{accounts[x].get('name', x)} ({x})"
            )
        else:
            st.info("No other members in the community yet. You can still create a group and add members later!")
            selected_members = []
        
        if st.button("🎉 Create Group", use_container_width=True, key="create_group_btn"):
            if not new_group_name.strip():
                st.warning("⚠️ Please enter a group name")
            elif groups_repo.exists(new_group_name):
                st.error(f"❌ A group with the name '{new_group_name}' already exists!")
            else:
                all_members = [st.session_state.user_email] + selected_members
                groups_repo.create(new_group_name, all_members, new_group_vibe, st.session_state.user_email)
                st.success(f"✅ Group '{new_group_name}' created! 🎉")
                st.balloons()
                st.rerun()
    
    with tab3:
        st.markdown("### Find Groups to Join")
        
        # Search functionality
        search_query = st.text_input("🔍 Search groups", key="find_groups_search", placeholder="Search by name or vibe...")
        
        if search_query:
            available_groups = groups_repo.search(search_query)
            # Filter out groups user is already in
            available_groups = {
                g: data for g, data in available_groups.items() 
                if st.session_state.user_email not in data.get("members", [])
            }
        else:
            available_groups = {
                g: data for g, data in groups.items() 
                if st.session_state.user_email not in data.get("members", [])
            }
        
        if available_groups:
            st.markdown(f"**Found {len(available_groups)} group(s)**")
            
            for group_name, group_data in available_groups.items():
                col1, col2 = st.columns([3, 1])
                with col1:
                    created_by = group_data.get('created_by', 'Unknown')
                    creator_name = accounts.get(created_by, {}).get('name', created_by) if created_by in accounts else created_by
                    member_count = len(group_data.get('members', []))
                    
                    st.markdown(f"""
                    <div class="group-card">
                        <h4>{group_name}</h4>
                        <p>{group_data.get('vibe', 'Casual meetup')}</p>
                        <small>👥 {member_count} member(s) • Created by {creator_name}</small>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Join", key=f"join_{group_name}", use_container_width=True):
                        groups_repo.add_member(group_name, st.session_state.user_email)
                        st.success(f"✅ You joined '{group_name}'! 🎉")
                        st.rerun()
        else:
            if search_query:
                st.info(f"No groups found matching '{search_query}'. Try a different search term or create a new group!")
            else:
                st.info("No other groups available to join. Why not create one?")